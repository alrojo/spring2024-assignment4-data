# 2.2
pytest -k test_extract_text_from_html_bytes

# 2.3
pytest -k test_identify_language

# 2.4
pytest -k test_mask_emails
pytest -k test_mask_phones
pytest -k test_mask_ips

# 2.5
pytest -k test_classify_nsfw
pytest -k test_classify_toxic_speech

# 2.6
pytest -k test_gopher

# 2.7
pytest -k test_classify_quality

# 3.1
pytest -k test_exact_line_deduplication

# 3.2
pytest -k test_minhash_deduplication
