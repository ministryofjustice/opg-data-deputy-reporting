variable "environment" {
  type = string
}

variable "aws_subnet_ids" {
  type = list(string)
}

variable "target_environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "lambda_prefix" {
  type = string
}

variable "handler" {
  type = string
}

variable "lambda_function_subdir" {
  type = string
}
