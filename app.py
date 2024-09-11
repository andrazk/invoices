from flask import Flask, request, render_template
import pdfplumber
from openai import OpenAI
import json
import base64
import qrcode
from io import BytesIO
import os
import httpx
from pydantic import BaseModel
from datetime import date

client = OpenAI()

app = Flask(__name__)


class InvoiceExtraction(BaseModel):
    invoice_number: str
    invoice_date: str
    due_date: str
    total_amount: str
    total_amount_currency: str
    bank_account: str
    bank_name: str
    issuer_name: str
    issuer_address: str
    issuer_zip_code: str
    issuer_city: str
    service_name: str
    reference_number: str


def botpoison(solution):
    data = {"secretKey": os.environ.get("BOTPOISON_SECRET_KEY"), "solution": solution}

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    try:
        response = httpx.post(
            "https://api.botpoison.com/verify", json=data, headers=headers
        )
        response_data = response.json()

        if response_data["ok"]:
            return True
        else:
            return False

    except httpx.RequestError as e:
        print(f"Botpoison Request failed: {e}")

    return False


def convertDateToDDMMLLLL(date_str):
    try:
        parts = date_str.split("-")
        return f"{parts[2]}.{parts[1]}.{parts[0]}"
    except Exception as e:
        print(f"Error: {e}")
        return None


def generatePrompt(text):
    p = """
    Below is a content of an invoice. Extract the following information from the invoice:
    - invoice number
    - invoice date
    - due date
    - total amount
    - bank account number (IBAN)
    - bank name
    - issuer name
    - issuer address
    - issuer zip code
    - issuer city
    - service or product name
    - reference number

    Reply with the extracted information in the JSON format. For example:

    {{
        "invoice_number": "123456",
        "invoice_date": "2021-01-01",
        "due_date": "2021-01-31",
        "total_amount": "1337.80",
        "total_amount_currency": "EUR",
        "bank_account": "SI56 1234 5678 9012 3456",
        "bank_name": "Bank of Slovenia",
        "issuer_name": "Podjetje d.o.o.",
        "issuer_address": "Ulica 123",
        "issuer_zip_code": "1000",
        "issuer_city": "Ljubljana",
        "service_name": "Programiranje",
        "reference_number": "SI00 20230922"
    }}

    General guidelines:

    - Use the date format YYYY-MM-DD for all dates.
    - Try to shorten service name to 50 characters or less, but try to keep it as descriptive as possible.
    - Don't return example values, but the actual values from the invoice. If not sure about the value, leave it empty.
    - Reference number should start with SIXX, or RFXX (XX is a number between 00 and 99) followed by space. 
        If the reference number is in the invoice, but without the prefix, follow this rules:
            - If Issuer is from Slovenia, add SI00 in front of the reference number
            - If Issuer is from EU, add RF00 in front of the reference number

    ```
    {text}
    ```
    """

    return p.format(text=text)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if not botpoison(request.form["_botpoison"]):
        # Botpoison detected a bot
        # Return http code 418 (I'm a teapot)
        return "I'm a teapot", 418

    if "file" not in request.files:
        return "No file part"

    pdf_file = request.files["file"]

    if pdf_file.filename == "":
        return "No selected file"

    if pdf_file:
        text = ""

        with pdfplumber.open(pdf_file) as pdf:
            for i, page in enumerate(pdf.pages):
                text += f"\n\n PAGE {i+1} \n\n"
                text += page.extract_text(layout=True)

        prompt = generatePrompt(text)

        # Use the Pydantic model `InvoiceExtraction` to parse the response
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at structured data extraction. You will be given unstructured text from an invoice and should convert it into the given structure.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=InvoiceExtraction,
        )

        # Parse the structured response using Pydantic
        invoice_data = completion.choices[0].message.parsed

        # Create a list of lines for UPN QR code generation
        lines = [
            "UPNQR",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            f"{int(float(invoice_data.total_amount.replace(',', '.')) * 100):011d}",
            "",
            "",
            "GDSV",
            invoice_data.service_name,
            convertDateToDDMMLLLL(invoice_data.due_date),
            invoice_data.bank_account.replace(" ", ""),
            invoice_data.reference_number,
            invoice_data.issuer_name,
            invoice_data.issuer_address,
            f"{invoice_data.issuer_zip_code} {invoice_data.issuer_city}",
        ]

        # Calculate character count
        charcount = sum(len(line) for line in lines)

        # Create the data string
        data_string = "\n".join(lines) + f"{charcount:03d}\n\n"

        # Create the QR code
        qr = qrcode.QRCode(
            version=15,  # Forced version
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(data_string)
        qr.make(fit=True)

        # Create a QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Save the QR code image to a BytesIO buffer
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")

        qr_image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return f"""
        <pre>
        {text}
        ------
        {completion.choices[0].message.content}
        </pre>

        <img src="data:image/png;base64,{qr_image_base64}" alt="UPN QR Code" width="600">
        """


if __name__ == "__main__":
    app.run(debug=True)
