output "lambda_arn" {
  description = "The ARN for your lambda function"
  value       = aws_lambda_function.lambda_function.arn
}

output "lambda_name" {
  description = "The unique name for your lambda function"
  value       = aws_lambda_function.lambda_function.function_name
}