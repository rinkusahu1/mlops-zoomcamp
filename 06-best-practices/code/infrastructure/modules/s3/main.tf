resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.bucket_name
  force_destroy = true
}

# name of the bucket
output "name" {
  value = aws_s3_bucket.s3_bucket.bucket
}
