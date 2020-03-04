output "lambda" {
  description = "The lambda function"
  value       = aws_lambda_function.lambda_function
}

output "lambda_arn" {
  value = aws_lambda_function.lambda_function.arn
}
