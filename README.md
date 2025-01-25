# flask-erc20-api
<p> <b>- pip install -r requirements.txt </b> </p>
<p> <b> - run code </b> </p>
<p> <b> - open browser/postman/curl </b> </p>
<p> <b> - use requests below: </b> </p>

<i> POST http://localhost:8080/get_balance_batch </i>
  Body: {"addresses": ["example", "example2"]}

<i> GET http://localhost:8080/get_balance?address=example_address </i> 

<i> GET http://localhost:8080/get_erc20_balance?token_address=0xTokenAddress&user_address=UserAddress </i>
