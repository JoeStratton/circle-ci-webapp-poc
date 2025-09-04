# ECS Cluster with cost optimization
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-cluster"
  })
}

# Security Group for ECS tasks
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "${var.project_name}-ecs-tasks"
  vpc_id      = data.aws_vpc.default.id
  description = "Security group for ECS tasks"

  ingress {
    description      = "HTTP from anywhere"
    protocol         = "tcp"
    from_port        = 5000
    to_port          = 5000
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    description      = "All outbound traffic"
    protocol         = "-1"
    from_port        = 0
    to_port          = 0
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-ecs-sg"
  })
}

# CloudWatch Log Group for ECS (minimal retention to save costs)
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.project_name}-task"
  retention_in_days = var.cloudwatch_log_retention_days

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-logs"
  })
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "${var.project_name}-app"
      image = "${aws_ecr_repository.app_repo.repository_url}:latest"

      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "FLASK_ENV"
          value = "production"
        },
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "DB_HOST"
          value = "localhost"
        },
        {
          name  = "DB_PORT"
          value = "5432"
        },
        {
          name  = "DB_NAME"
          value = "appdb"
        },
        {
          name  = "DB_USERNAME"
          value = var.database_username
        },
        {
          name  = "DB_PASSWORD"
          value = var.database_password
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "app"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"]
        interval    = 30
        timeout     = 10
        retries     = 3
        startPeriod = 90
      }

      dependsOn = [
        {
          containerName = "${var.project_name}-postgres"
          condition     = "HEALTHY"
        }
      ]

      essential = true
    },
    {
      name  = "${var.project_name}-postgres"
      image = "postgres:13"

      environment = [
        {
          name  = "POSTGRES_DB"
          value = "appdb"
        },
        {
          name  = "POSTGRES_USER"
          value = var.database_username
        },
        {
          name  = "POSTGRES_PASSWORD"
          value = var.database_password
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "postgres"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "pg_isready -U ${var.database_username} -d appdb"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }

      essential = true
    }
  ])

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-task-def"
  })
}

# ECS Service (cost-optimized)
resource "aws_ecs_service" "app" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1 # Single instance for cost optimization
  launch_type     = var.enable_fargate_spot ? null : "FARGATE"

  # Ignore task_definition changes since CircleCI manages deployments
  lifecycle {
    ignore_changes = [task_definition]
  }

  # Use Fargate Spot for additional cost savings when enabled
  dynamic "capacity_provider_strategy" {
    for_each = var.enable_fargate_spot ? [1] : []
    content {
      capacity_provider = "FARGATE_SPOT"
      weight            = 100
    }
  }

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = data.aws_subnets.default.ids
    assign_public_ip = true
  }

  deployment_controller {
    type = "ECS"
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-service"
  })

  # Ensure task definition is updated before service
  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy,
    aws_cloudwatch_log_group.ecs_logs
  ]
}
