# Python code

* Server
    - **Database creation**: `python3 python_code/python/vendor.py <PORT> new`

* Vendor
    - **Registration**: `python3 python_code/python/vendor.py <PORT> request`  
    The vendor requests from the server a fresh and unique $csr_{id}$ and saves it in its DB
    - **Enrollment**: `python3 python_code/python/vendor.py <PORT> add`  
    The vendor computes $P$ and $h_{seal}$ for  each $seal$ and sends them to the server which in its turn checks from uniquenesss before save

## Notes
Run the server with:
```sh
python3 python_code/python/server.py <port> new
```
or:
```sh
python3 python_code/python/server.py <port> add
```
To enroll the `responses` folder run 
```sh
python3 python_code/python/enroll.py <port>
```