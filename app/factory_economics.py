"""Transparent synthetic production math. Illustrative assumptions, not manufacturing data."""
from dataclasses import dataclass
from math import ceil

@dataclass(frozen=True)
class Assumptions:
    sugar_g_per_bean: float = 1.5
    flavor_g_per_bean: float = 0.075
    pigment_g_per_bean_at_full: float = 0.012
    sugar_cost_per_kg: float = 1.8
    flavor_cost_per_kg: float = 26.0
    pigment_cost_per_kg: float = 90.0
    packaging_cost_per_bean: float = 0.006
    oven_capacity: int = 1200
    molding_capacity: int = 1600
    packing_capacity: int = 2000
    minutes_per_cycle: float = 18

A = Assumptions()

def estimate(quantity=1000, intensity=65, speed='normal', valid=True):
    if not isinstance(quantity,int) or not 100 <= quantity <= 5000:
        raise ValueError('Batch size must be between 100 and 5000')
    if not isinstance(intensity,int) or not 0 <= intensity <= 100:
        raise ValueError('Intensity must be from 0 to 100')
    if speed not in {'slow','normal','fast'}:
        raise ValueError('Unknown processing speed')
    grams={'sugar':round(quantity*A.sugar_g_per_bean,2),
           'flavor':round(quantity*A.flavor_g_per_bean,2),
           'pigment':round(quantity*A.pigment_g_per_bean_at_full*intensity/100,2)}
    costs={'sugar':grams['sugar']/1000*A.sugar_cost_per_kg,
           'flavor':grams['flavor']/1000*A.flavor_cost_per_kg,
           'pigment':grams['pigment']/1000*A.pigment_cost_per_kg,
           'packaging':quantity*A.packaging_cost_per_bean}
    limits={'Cooking':A.oven_capacity,'Shaping':A.molding_capacity,'Packaging':A.packing_capacity}
    bottleneck=min(limits,key=limits.get)
    cycles=ceil(quantity/limits[bottleneck])
    multiplier={'slow':1.4,'normal':1.0,'fast':0.75}[speed]
    return {'quantity':quantity,'intensity':intensity,'speed':speed,'valid':valid,
      'materials_g':grams,'material_cost_units':round(sum(costs.values()),2),
      'cost_components':{k:round(v,2) for k,v in costs.items()},
      'bottleneck':bottleneck,'max_batch_capacity':limits[bottleneck],
      'cycles':cycles,'minutes':ceil(cycles*A.minutes_per_cycle*multiplier) if valid else None,
      'warnings':(['Synthetic model only; machine settings and product safety unverified.']+
         (['Fast operation has no independent quality verification.'] if speed=='fast' else [])+
         (['Disconnected production route; no finished batch.'] if not valid else []))}
