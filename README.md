sudo apt update
sudo apt-get update
sudo apt upgrade -y
sudo apt install git curl unzip tar make sudo vim wget -y
git clone "genai_idea_incubators"
sudo apt install python3-pip
pip3 install -r requirements.txt
#Temporary running
python3 -m streamlit run app.py
#Permanent running
nohup python3 -m streamlit run app.py
