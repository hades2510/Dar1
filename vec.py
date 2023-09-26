import math

def add(p1, p2):
    return {
        'x': p1['x'] + p2['x'],
        'y': p1['y'] + p2['y']
    }

def sub(p1, p2):
    return {
        'x': p1['x'] - p2['x'],
        'y': p1['y'] - p2['y']
    }

def dot(p1, p2):
    return p1['x']*p2['x'] + p1['y']*p2['y']

def proj(p1, p2):
    k = dot(p1,p2)/ dot(p2,p2)
    
    return {
        'x': k * p2['x'],
        'y': k * p2['y']
    }

def dist(p1, p2):
    return math.sqrt(dist_squared(p1, p2))

def dist_squared(p1, p2):
    return (p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2

def magnitude(p):
    return math.sqrt(magnitude_squared(p))

def magnitude_squared(p):
    return p['x']**2 + p['y']**2