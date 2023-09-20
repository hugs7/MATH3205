import gurobipy as gp
import numpy
import csv
 
with open('CovMatrixNorm.csv', 'r') as f:
    reader = csv.reader(f,delimiter=',')
    temp1 = list(reader)

W = [[float(j) for j in i] for i in temp1]

NumAsset=20

N = range(NumAsset)

# Small adjustment to make positive definite
for i in N:
    W[i][i] += 0.005

R=[
1.071877684,
1.075411639,
1.10823578,
1.07868473,
1.103370352,
1.312741894,
1.117739229,
1.058670271,
1.178226399,
1.063677793,
1.133877788,
1.128557584,
1.010831389,
1.096413424,
1.120902431,
1.01264185,
1.061801832,
1.131959114,
1.119030185,
1.115390706
]

# Add the risk free asset
RiskFree=True
if RiskFree:
    R.append(1)
    for i in N:
        W[i].append(0.0)
    N = range(NumAsset+1)
    W.append([0.0 for i in N])


Names=[
'AMC',
'ANZ',
'BHP',
'BXB',
'CBA',
'CSL',
'GMG',
'IAG',
'MQG',
'NAB',
'NCM',
'RIO',
'SCG',
'SUN',
'TCL',
'TLS',
'WBC',
'WES',
'WOW',
'WPL',
'CSH'
]

S = range(10000)
numpy.random.seed(95)

# Generate a random sample
RS = numpy.random.multivariate_normal(R,W,len(S)).tolist()
