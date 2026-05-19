provider "aws" {
  region = "us-east-1"
}

# ---------------- VPC ----------------

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}

# ---------------- SUBNETS ----------------

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
}

# ---------------- INTERNET GATEWAY ----------------

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

# ---------------- ROUTE TABLE ----------------

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "a1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "a2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# ---------------- SECURITY GROUP ----------------

resource "aws_security_group" "ecs_sg" {
  name   = "ecs-security-group"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------- CLOUDWATCH ----------------

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/complaint-app"
  retention_in_days = 7
}

# ---------------- ECR ----------------

resource "aws_ecr_repository" "repo" {
  name = "complaint-app"
}

# ---------------- IAM ROLE ----------------

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Action = "sts:AssumeRole"

        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role = aws_iam_role.ecs_task_execution_role.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ---------------- ECS CLUSTER ----------------

resource "aws_ecs_cluster" "main" {
  name = "complaint-cluster"
}

# ---------------- APPLICATION LOAD BALANCER ----------------

resource "aws_lb" "app_alb" {
  name = "complaint-alb"

  internal = false

  load_balancer_type = "application"

  security_groups = [aws_security_group.ecs_sg.id]

  subnets = [
    aws_subnet.public_1.id,
    aws_subnet.public_2.id
  ]
}

# ---------------- TARGET GROUP ----------------

resource "aws_lb_target_group" "app_tg" {
  name = "complaint-tg"

  port = 8501

  protocol = "HTTP"

  target_type = "ip"

  vpc_id = aws_vpc.main.id

  health_check {
    path = "/"
  }
}

# ---------------- LISTENER ----------------

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app_alb.arn

  port = 80

  protocol = "HTTP"

  default_action {
    type = "forward"

    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

# ---------------- ECS TASK ----------------

resource "aws_ecs_task_definition" "app" {

  family = "complaint-task"

  network_mode = "awsvpc"

  requires_compatibilities = ["FARGATE"]

  cpu = "512"

  memory = "1024"

  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name = "complaint-container"

      image = "${aws_ecr_repository.repo.repository_url}:latest"

      essential = true

      portMappings = [
        {
          containerPort = 8501
          hostPort      = 8501
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = "/ecs/complaint-app"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# ---------------- ECS SERVICE ----------------

resource "aws_ecs_service" "app" {

  name = "complaint-service"

  cluster = aws_ecs_cluster.main.id

  task_definition = aws_ecs_task_definition.app.arn

  desired_count = 1

  launch_type = "FARGATE"

  network_configuration {

    subnets = [
      aws_subnet.public_1.id,
      aws_subnet.public_2.id
    ]

    security_groups = [
      aws_security_group.ecs_sg.id
    ]

    assign_public_ip = true
  }

  load_balancer {

    target_group_arn = aws_lb_target_group.app_tg.arn

    container_name = "complaint-container"

    container_port = 8501
  }

  depends_on = [
    aws_lb_listener.http
  ]
}