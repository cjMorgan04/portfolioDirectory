import numpy as np
from scipy.signal import savgol_filter
from scipy import optimize


def decayThreshold(I_smooth, V): 
    # this function will define where the high/low voltage regions are 

    # np.gradient computes central differences: (I[i+1] - I[i-1]) / (V[i+1] - V[i-1])
    slope = np.gradient(I_smooth, V) # this is dI/dV

    steepestIndex = np.argmin(slope) # np.argmin finds index where derivative is most negative (steepest drop)
    maxDecay = slope[steepestIndex]

    threshold = maxDecay/(2) # defines the max slope value which we still consider to be valid low voltage region  
    # I found that 1/2 returns the closest value of h compared to 1/e

    fastDecayRegion = slope <= threshold # creates an array of bools in our low v 
    slowDecayRegion = (slope >= threshold) & (np.arange(len(V)) > steepestIndex) # creates bool array for high v region 


    return fastDecayRegion, slowDecayRegion


def linearFit(x, y):
    # a linear fit (y = mx + b) will allow us to find slopes and y intercepts of three relevent data sets
    # the first two will be for our decay regions 
    # the last will be for determining h

    slope, y_intercept = np.polyfit(x, y, 1)


    if len(x) >= 30:    # I found that this may accidentally cut off too many points for this experiment but it may be useful for later labs
        # a residual verification may be done in case any current reading deviates too far  
        # this is accomplished by using a predicted linear function as a referrence 

        # firstly we need to see how far away each oberved point is away from the predicted ones
        y_predicted = slope * x + y_intercept
        residuals = np.abs(y - y_predicted) # np.abs returns an absolute value 

        # next we must define a threshold similar to 1/e earlier 
        # the following code says that the only valid points are those whithin 
        # 10% of the range of values observed in current, essentially we claim that the 
        # displacment of individual points from predicted should reflect the total spread of our current data
        validPoints = residuals <= (0.1 * np.ptp(y))
        slope, y_intercept = np.polyfit(x[validPoints], y[validPoints], 1)

   
    return slope, y_intercept




# to propagate our measurement errors of photocurrent into stopping voltage 
# I decided to use the same method used in the example lab report but made some moodifications to find V stopping uncertainty

# Source - https://stackoverflow.com/a/21844726
# Posted by Pedro M Duarte, modified by community. See post 'Timeline' for change history
# Retrieved 2026-09-04, License - CC BY-SA 4.0

def fit_bootstrap(p0, datax, datay, function, yerr_systematic=0.0):

    errfunc = lambda p, x, y: function(x,p) - y

    # Fit first time
    pfit, perr = optimize.leastsq(errfunc, p0, args=(datax, datay), full_output=0)


    # Get the stdev of the residuals
    residuals = errfunc(pfit, datax, datay)
    sigma_res = np.std(residuals)

    sigma_err_total = np.sqrt(sigma_res**2 + yerr_systematic**2)

    # 100000 random data sets are generated and fitted
    ps = []
    for i in range(100000):

        randomDelta = np.random.normal(0., sigma_err_total, len(datay))
        randomdataY = datay + randomDelta

        randomfit, randomcov = \
            optimize.leastsq(errfunc, p0, args=(datax, randomdataY),\
                             full_output=0)

        ps.append(randomfit) 

    ps = np.array(ps)

    return ps
   
# the code below will return slope and intercept uncertainty unlike the 
# code above which I used to do Voltage error calculations
def fit_bootstrap_full(p0, datax, datay, function, yerr_systematic=0.0):

    errfunc = lambda p, x, y: function(x,p) - y

    # Fit first time
    pfit, perr = optimize.leastsq(errfunc, p0, args=(datax, datay), full_output=0)


    # Get the stdev of the residuals
    residuals = errfunc(pfit, datax, datay)
    sigma_res = np.std(residuals)

    sigma_err_total = np.sqrt(sigma_res**2 + yerr_systematic**2)

    # 100000 random data sets are generated and fitted
    ps = []
    for i in range(100000):

        randomDelta = np.random.normal(0., sigma_err_total, len(datay))
        randomdataY = datay + randomDelta

        randomfit, randomcov = \
            optimize.leastsq(errfunc, p0, args=(datax, randomdataY),\
                             full_output=0)

        ps.append(randomfit) 

    ps = np.array(ps)
    mean_pfit = np.mean(ps,0)

    # You can choose the confidence interval that you want for your
    # parameter estimates: 
    Nsigma = 2. # 1sigma gets approximately the same as methods above
                # 1sigma corresponds to 68.3% confidence interval
                # 2sigma corresponds to 95.44% confidence interval
    err_pfit = Nsigma * np.std(ps,0) 

    pfit_bootstrap = mean_pfit
    perr_bootstrap = err_pfit
    return pfit_bootstrap, perr_bootstrap 
 