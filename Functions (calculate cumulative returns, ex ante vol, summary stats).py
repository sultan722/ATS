def get_cum_returns(series, data = 'returns', ret_type = 'arth', dtime = 'monthly'):
    """Returns cumulative performance of the price/return series (hypothetical growth of $1)
    parameters:
        series: timeseries data with index as datetime
        data: (optional) returns or prices str
        ret_type: (optional) 'log' or 'arth'
        dtime: (optional) str, 'monthly', 'daily'
    returns:
        series (cumulative performance)
        """
    if (isinstance(series, pd.core.series.Series)) and (isinstance(series.index, pd.DatetimeIndex)):
        pass
    else:
        raise NotImplementedError('Data Type not supported, should be time series')

    series.dropna(inplace = True)


    if data == 'returns':
        rets = series
        if ret_type == 'arth': 
            cum_rets = (1+rets).cumprod()
        elif ret_type == 'log':
            cum_rets = np.exp(rets.cumsum())

        if dtime == 'daily':
            cum_rets_prd = cum_rets
            cum_rets_prd.iloc[0] = 1

        elif dtime == 'monthly':
            cum_rets_prd = cum_rets.resample('BM').last().ffill()
            cum_rets_prd.iloc[0] = 1

    elif data == 'prices':
        cum_rets = series/series[~series.isnull()][0]

        if dtime == 'daily':
            cum_rets_prd = cum_rets
        elif dtime == 'monthly':
            cum_rets_prd = cum_rets.resample('BM').last().ffill()

    return cum_rets_prd
    
    
    def get_exante_vol(series, alpha = 0.05, com = 60, dtime = 'monthly', dtype = 'returns'):

    """Calculates annualized ex ante volatility based on the method of Exponentially Weighted Average
    This method is also know as the Risk Metrics, where the instantaneous volatility is based on past volatility
    with some decay
    parameters:
    -------
        series: pandas series
        com: center of mass (optional) (int)
        dtime: str, (optional), 'monthly', 'daily', 'weekly'
    returns:
        ex-ante volatility with time index"""
        
    if (isinstance(series, pd.core.series.Series)) and (isinstance(series.index, pd.DatetimeIndex)):
        pass
    else:
        raise NotImplementedError('Data Type not supported, should only be timeseries')
    if dtype == 'prices':
        series = get_rets(series, kind = 'arth', freq = 'd')

    vol = series.ewm(alpha = alpha, com = com).std()
    ann_vol = vol * np.sqrt(261)

    if dtime == 'daily':
        ann_vol_prd = ann_vol

    elif dtime == 'monthly':
        ann_vol_prd = ann_vol.resample('BM').last().ffill()

    elif dtime == 'weekly':
        ann_vol_prd = ann_vol.resample('W-Fri').last().ffill()


    return ann_vol_prd

def get_stats(returns, dtime = 'monthly'):
    """Calculates annualized mean, annualized volatility and annualized sharpe ratio
    parameters:
        returns: series or dataframe of retunrs
        dtime: (optional) 'monthly' or 'daily'
    returns:
        tuple of stats(mean, std and sharpe)"""
    if (isinstance(returns, pd.core.series.Series)) | (isinstance(returns, pd.core.frame.DataFrame)):
        mean = returns.mean()
        std = returns.std()
    else:
        try:
            mean = np.mean(returns)
            std = np.std(returns)
        except:
            raise TypeError
    if dtime == 'monthly':
        mean = mean * 12
        std = std * np.sqrt(12)
    elif dtime == 'daily':
        mean = mean * 252
        std = std * np.sqrt(252)

    sr = mean/std

    return (mean, std, sr)
