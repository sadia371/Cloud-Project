output "alb_url" {
  value = aws_lb.app_alb.dns_name
}

output "ecr_url" {
  value = aws_ecr_repository.repo.repository_url
}