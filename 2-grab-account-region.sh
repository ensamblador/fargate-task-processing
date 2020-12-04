echo "export AWS_DEFAULT_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region)" >> ~/.bashrc

echo "export AWS_ACCOUNT_ID=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r .accountId)" >> ~/.bashrc

source ~/.bashrc

echo "Region = sh ${AWS_DEFAULT_REGION}"
echo "AccountId = ${AWS_ACCOUNT_ID}"