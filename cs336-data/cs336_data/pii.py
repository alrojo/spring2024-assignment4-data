import re

email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
phone_number_pattern = re.compile(r'(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}')
ip_addr_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

def mask_emails(text: str) -> tuple[str, int]:
    return re.subn(email_pattern, "|||EMAIL_ADDRESS|||", text)

def mask_phone_numbers(text: str) -> tuple[str, int]:
    return re.subn(phone_number_pattern, "|||PHONE_NUMBER|||", text)

def mask_ips(text: str) -> tuple[str, int]:
    return re.subn(ip_addr_regex, "|||IP_ADDRESS|||", text)

if __name__=='__main__':
    for i in range(1, 20+1):
        file_path = f"out/extract_warc{i}.txt" 
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read().strip("\n")
            text, num_emails = mask_emails(text)
            text, num_phone_numbers = mask_phone_numbers(text)
            text, num_ips = mask_ips(text)
            print("@@@@@@@@@@@@")
            print(text)
            print("@@@@@@@@@@@@")
            print(f"{i}: emails: {num_emails}, phone numbers: {num_phone_numbers}, ips: {num_ips}")
            _ = input("next?")
