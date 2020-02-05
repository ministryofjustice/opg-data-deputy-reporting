output data_deputy_reporting {
  description = "The data deputy reporting role"
  value       = aws_iam_role.data_deputy_reporting
}

output access_policy {
  description = "The access policy to attach"
  value       = aws_iam_policy.access_policy
}
