"""Owner-authenticated synthetic episode creation, not a general database mutation API."""
import hmac
import os
from .factory_episode import create_episode, read_episode
from .graph import validate_id

def authorize(token):
    secret=os.getenv('FG_EPISODE_WRITE_TOKEN','')
    return len(secret)>=32 and isinstance(token,str) and hmac.compare_digest(secret,token)

def create_owned_episode(payload, token):
    if not authorize(token):raise PermissionError('Owner authorization required')
    if not isinstance(payload,dict) or set(payload)!={'id','quantity','stock','prior','evidence'}:
        raise ValueError('Unsupported episode request')
    ident=validate_id(payload['id'])
    quantity=payload['quantity']
    stock=payload['stock']
    prior=payload['prior']
    evidence=payload['evidence']
    if type(quantity) is not int or not 100<=quantity<=5000:raise ValueError('Invalid quantity')
    if type(stock) not in (int,float) or not 1<=stock<=10:raise ValueError('Invalid inventory')
    if prior is not None:validate_id(prior)
    if evidence not in ('UNVERIFIED','EQUIPMENT_CERTIFIED'):raise ValueError('Invalid evidence state')
    return create_episode(ident,quantity,stock,prior,evidence)
