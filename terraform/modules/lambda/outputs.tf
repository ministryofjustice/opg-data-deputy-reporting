output "lambda_arn" {
  description = "The ARN for your lambda function"
  value       = aws_lambda_function.lambda_function.arn
}

output "lambda_name" {
  description = "The unique name for your lambda function"
  value       = aws_lambda_function.lambda_function.function_name
}

output "lambda_invoke_arn" {
  description = "The unique name lambda invoke arn"
  value       = aws_lambda_function.lambda_function.invoke_arn
}