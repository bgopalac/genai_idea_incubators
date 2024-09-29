sudo apt update

sudo apt-get update

sudo apt upgrade -y

sudo apt install git curl unzip tar make sudo vim wget -y

git clone "genai_idea_incubators"

sudo apt install python3-pip

python3 -m venv venv 

source venv/bin/activate 

pip3 install -r requirements.txt

nano .env

#Temporary running
python3 -m streamlit run app.py

#Permanent running
nohup python3 -m streamlit run app.py

#Permanent running
nohup python3 -m streamlit run app.py
