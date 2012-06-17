from cloudydave import cloudydave
from config import checks, datastores

cd = cloudydave(checks, datastores)
cd.run_checks()
