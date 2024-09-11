# Invoice Extraction and QR Code Generator

This project is a web application built with Flask that allows users to upload PDF invoices. The application extracts key information from the invoices such as invoice number, total amount, due date, and bank details. It then generates a UPN QR code based on the extracted data. The app also integrates with OpenAI’s GPT-4 model to structure and validate the extracted data using a predefined schema.

## Features

- Upload PDF invoices and extract important information such as:
  - Invoice number
  - Invoice date
  - Due date
  - Total amount
  - Bank account (IBAN)
  - Issuer details
  - Reference number
- Generate a UPN QR code based on the extracted invoice data.
- Secure form submissions with Botpoison integration to detect and block bots.
- Asynchronous HTTP requests using `httpx`.
- Data validation and structuring using Pydantic models.

## Tech Stack

- **Python**: Flask for the web framework and OpenAI API integration.
- **OpenAI GPT-4**: Used for structured data extraction from invoice content.
- **Pydantic**: For data validation and structuring.
- **pdfplumber**: To parse PDF files and extract text from invoices.
- **qrcode**: To generate the UPN QR code.
- **httpx**: For making HTTP requests.

## Getting Started

Follow the steps below to set up and run the project locally.

### Prerequisites

- Python 3.10 or higher
- [OpenAI API Key](https://platform.openai.com/signup/)
- Botpoison API Key (for bot protection)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/andrazk/invoices.git
   ```

2. **Set up a virtual environment:**

   It's recommended to use a virtual environment to manage your dependencies.

   On macOS/Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install the dependencies:**

   After activating the virtual environment, install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the project directory and add your API keys:

   ```bash
   BOTPOISON_SECRET_KEY=your_botpoison_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ```

   Make sure to replace `your_botpoison_secret_key` and `your_openai_api_key` with your actual keys.

### Running the Application

1. **Start the Flask development server:**

   ```bash
   flask run
   ```

   The application will now be accessible at `http://127.0.0.1:5000/`.

2. **Upload an Invoice:**

   - Visit the homepage of the application.
   - Upload a PDF file containing the invoice.
   - The application will extract key information and generate a UPN QR code based on the extracted data.

### Testing the Application

To test that the application is working correctly:

- Upload a sample invoice in PDF format.
- Verify that the extracted data is correctly displayed.
- Check if the generated QR code is accurate.

### Running Tests

You can write and run tests to ensure the application works as expected. If there are any test cases provided, you can run them using:

```bash
pytest
```

## Deploy to Vercel

After setting up the vercel.json file and adding the environment variables, you can deploy your app by running:

```bash
vercel
```

This will deploy the app and provide you with a URL where you can access it.

### License

This project is licensed under the MIT License.
