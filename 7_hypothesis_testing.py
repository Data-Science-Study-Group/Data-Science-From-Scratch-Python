#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 06:48:40 2019
@author: Neeraj
Description: This code performs basic hypothesis testing in Python. 
Reference: Chapter 6 : Hypothesis and Inference
"""
import os
os.chdir('/Users/apple/Documents/Courses/DSS')

from typing import Tuple
import math

def normal_approximation_binomial(n: int, p: float) -> Tuple[float,float]:
    """Estimates mu and sigma for a specified p and n"""
    mu = n*p
    sigma = math.sqrt(n*p*(1-p))
    
#It's above threshold if it's not below the threshold
def normal_probability_above(lo: float,
                             mu: float = 0,
                             sigma: float = 1) -> float:
    return 1 - normal_cdf(lo, mu, sigma)

#It's in between if it is less than hi but greater than lo
def normal_probability_between(lo: float,
                               hi: float,
                               mu: float = 0,
                               sigma: float = 1) -> float:
    return normal_cdf(hi, mu, sigma) - normal_cdf(lo, mu, sigma)

# It's outside if not in between
def normal_probability_outside(lo: float,
                               hi: float,
                               mu: float = 0,
                               sigma: float = 1) -> float:
    return 1 - normal_probability_between(lo, high, mu, sigma)