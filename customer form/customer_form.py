from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
from google.oauth2 import id_token
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# Replace with your client ID obtained from the Google Cloud Console
CLIENT_ID = '738497011546-59alpin625v8uum6m0eb4t2gfdqfmne5.apps.googleusercontent.com'

@app.route('/')
def directives():
    return render_template('directives.html')

@app.route('/terms', methods=['GET', 'POST'])
def terms_and_conditions():
    if request.method == 'POST':
        # Check if the user accepted the terms
        if request.form.get('accept') == 'yes':
            # Redirect to the form page with GET method
            return redirect('/form')
    return render_template('terms.html')

@app.route('/login')
def login():
    # Render the login page template
    return render_template('login.html')

# Handle the authentication callback from the Google sign-in page
@app.route('/auth_callback')
def auth_callback():
    # Get the authorization token from the request query parameters
    token = request.args.get('token')

    if token:
        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer.')
            
            # Store the token in a cookie for subsequent requests
            response = redirect('/form')
            response.set_cookie('token', token)
            return response
        
        except ValueError:
            # Handle the error if the token is invalid or the issuer is not trusted
            return redirect('/error')

    # Redirect to the login page if the token is not present
    return redirect('/login')

@app.route('/form', methods=['GET', 'POST'])
def customer_form():
    if request.method == 'POST':
        # Process the form data
        # ...
        # Redirect to the preview page with POST method
        return redirect('/preview', code=307)
    else:
        # Display the form page with GET method
        return render_template('form.html')

@app.route('/preview', methods=['POST'])
def preview():
    # Process the form data
    name = request.form.get('name')
    twitter_link = request.form.get('twitter_link')
    facebook_link = request.form.get('facebook_link')
    project_details = request.form.get('project_details')
    deadline = request.form.get('deadline')
    course_year_grade = request.form.get('course_year_grade')
    budget = request.form.get('budget')
    payment_mode = request.form.get('payment_mode')
    email = request.form.get('email')

    # Perform any additional processing or saving of data
    # You can add your own logic here to handle the form submission

    # Create the email message
    msg = EmailMessage()
    msg['Subject'] = 'Customer Form Submission'
    msg['From'] = 'arthcommissions@gmail.com'  # Replace with your email address
    msg['To'] = 'arthcommissions@gmail.com'  # Replace with the recipient's email address
    msg.add_header('Bcc', email)  # Add the customer's email as a Bcc recipient

    # Set the email content
    email_content = f"Name: {name}\nTwitter Link: {twitter_link}\n..."  # Add all the form fields
    msg.set_content(email_content)

    # Send the email using Gmail API with OAuth 2.0 authentication
    token = request.cookies.get('token')
    if token:
        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer.')
            
            # Use the authorized email address for sending the email
            authorized_email = id_info['email']
            
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login(authorized_email, 'Riyamori2026')  # Replace with your email credentials
                smtp.send_message(msg)

            # Redirect to the success page with POST method
            return redirect('/success')
        
        except ValueError:
            # Handle the error if the token is invalid or the issuer is not trusted
            return redirect('/error')
    
    # Redirect to the login page if the user is not authenticated
    return redirect('/login')

@app.route('/success', methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        # Process the form data
        # ...
        return render_template('success.html')
    else:
        # Display the success page with GET method
        return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
