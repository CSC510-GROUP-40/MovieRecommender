## Tech Stack 👨‍💻

<details>
<summary>Python</summary>
Python is our core programming language, ideal for building the recommendation engine with its simplicity and power.
</details>

<details>
<summary>Flask</summary>
Flask serves as the backbone of our web app, making it easy to create and manage a dynamic and interactive user interface.
</details>

<details>
<summary>HTML & CSS</summary>
HTML structures our content, while CSS styles it to make sure you enjoy a sleek and user-friendly design.
</details>

<details>
<summary>JavaScript</summary>
JavaScript adds interactivity to our app, giving users a seamless experience.
</details>

## Setup and Installation ⚙️

To get started with StreamR:

- Python 3.5+
- pip
- Code Formatter - black
    `pip install black`
- Code Linter - Pylance (install it in VS Code)

### Install Dependencies
After cloning, install dependencies with:
```bash
pip install -r requirements.txt
```
#### Create Google Client Credentials
- First, note that you will need a Google Account. You already have one if you use Gmail.

- Go to the [Google developers credentials page](https://console.developers.google.com/apis/credentials).

- Once in, you may be prompted to agree to their terms of service. Should you agree to those, press the Create credentials button on the next page. Select the option for OAuth client ID:
![Google Credentials Page](docs/google_crendentials.jpg)
- Select the Web application option at the top. You can provide a name for the client in the Name field as well. The name you provide will be displayed to users when they are consenting to your application acting on their behalf.

- if you’ll be running your web application locally for now, so you can set the Authorized JavaScript origins to https://127.0.0.1:5000 and Authorized redirect URIs to https://127.0.0.1:5000/login/callback. This will allow your local Flask application to communicate with Google.

- Finally, hit Create and take note of the client ID and client secret. You’ll need both later. You may also download the config file as json and update you `.env` file with the required fields
## Getting Started
1. Run this command `cd Code/recommenderapp`
2. Create a `.env` file inside `Code/recommenderapp`  and paste the content as found in `.env.example`. Populate the fields with your own credentials

3. Run the application with:
   ```bash
   python -m flask run --debug
   ```
4. Visit `http://127.0.0.1:5000/` in your browser to start exploring!
5. To test the google sign in feature run the app with `python -m flask run --debug --cert=adhoc` and visit the app on `https://127.0.0.1:5000/`

#### GOOGLE CHROME SETTINGS FOR SSL
for ssl to work locally on google chrome, you will have to do the following settings within your chrome browser.
- open this URL on chrome chrome://flags/#allow-insecure-localhost
- set the Allow invalid certificates for resources loaded from localhost. and enable this by clicking on relaunch at the bottom right. see image below
![Google settings for SSL](docs/chrome.png)
- note that this settings is not required for firefox 
  
  
### Running Tests
1. Make sure pytest is installed on your system.
2. switch to the tests directortory: `cd MovieRecommender/Code/tests`.
3. Run the tests with `pytest`

![Starting App](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXhqdHRreDQ5NGd2MmY3NjB5dGhlbjNuNWU0MXlib3Q4bXp3eGxzayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2IudUHdI075HL02Pkk/giphy.gif)

## Documentation 📚
Check out the [Wiki documentation](https://github.com/Shravsssss/MovieRecommender/wiki) for detailed information on how StreamR works and how to contribute.



## Found a Bug? 🐛
We’d love to hear from you! Please [open an issue](https://github.com/Shravsssss/MovieRecommender/issues) if you find any bugs or have feature requests.


