# EFS File System for PostgreSQL persistent storage
resource "aws_efs_file_system" "postgres_data" {
  creation_token = "${var.project_name}-postgres-data"
  encrypted      = true
  performance_mode = "generalPurpose"
  throughput_mode  = "provisioned"
  provisioned_throughput_in_mibps = 100

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-postgres-data"
  })
}

# EFS Access Point for PostgreSQL data
resource "aws_efs_access_point" "postgres_data" {
  file_system_id = aws_efs_file_system.postgres_data.id
  posix_user {
    gid = 999 # postgres user group ID
    uid = 999 # postgres user ID
  }
  root_directory {
    path = "/postgres-data"
    creation_info {
      owner_gid   = 999
      owner_uid   = 999
      permissions = "755"
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-postgres-access-point"
  })
}

# EFS Mount Target Security Group
resource "aws_security_group" "efs_mount" {
  name_prefix = "${var.project_name}-efs-mount"
  vpc_id      = data.aws_vpc.default.id
  description = "Security group for EFS mount targets"

  ingress {
    description     = "NFS from ECS tasks"
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-efs-mount-sg"
  })
}

# EFS Mount Targets (all subnets to ensure ECS tasks can access EFS)
resource "aws_efs_mount_target" "postgres_data" {
  count           = length(data.aws_subnets.default.ids)
  file_system_id  = aws_efs_file_system.postgres_data.id
  subnet_id       = data.aws_subnets.default.ids[count.index]
  security_groups = [aws_security_group.efs_mount.id]
}
