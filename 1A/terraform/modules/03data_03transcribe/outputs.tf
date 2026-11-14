output "transcribe_vocabulary_name" {
  value = aws_transcribe_vocabulary.main.vocabulary_name
}

output "transcribe_filter_name" {
  value = aws_transcribe_vocabulary_filter.main.vocabulary_filter_name
}
