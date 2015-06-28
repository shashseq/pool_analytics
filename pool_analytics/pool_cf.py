from array import array
from datetime import date
from dateutil.relativedelta import *
from QuantLib import *
class PoolCF:
    def __init__(self):

        self.sched_interest=array('d')
        self.sched_principal=array('d')
        self.pool_interest=array('d')
        self.prepaid_principal=array('d')
        self.defaulted_principal=array('d')
        self.total_principal= array('d')
        self.total_cf=array('d')
        self.pmnt_dates=[]
        self.accrual_start_dates = []
        self.accrual_end_dates = []
        self.smm_arr = array('d')
        self.smd_arr = array('d')
        self.severity_arr = array('d')
        self.one_month = Period(1,Months)
        self.one_day=Period(1,Days)


        
    def generateSMM_SMD_Arr(self,pool,settledate,cpr,cdr,severity):
        exponent=1.0/12.0
        smm= 1 - pow(1.0 -(cpr/100.0),exponent)
        smd= 1 - pow(1.0 -(cdr/100.0),exponent)
        svr = severity/100.0

        for i in xrange(0,pool.wam):
            self.smm_arr.append(smm)
            self.smd_arr.append(smd)
            self.severity_arr.append(svr)
        
        del self.sched_interest[:]
        del self.sched_principal[:]
        del self.pool_interest[:]
        del self.prepaid_principal[:]
        del self.defaulted_principal[:]
        del self.total_principal[:]
        del self.total_cf[:]
        del self.pmnt_dates[:]
        del self.accrual_start_dates[:]
        del self.accrual_end_dates[:]
        
    def generatePmntSchedule(self,settledate,wam):
        sdate=settledate
        sdate=QuantLib.Date(25,sdate.month(),sdate.year())
        
        for i in xrange(0,wam):
            sdate=sdate+self.one_month
            self.pmnt_dates.append(sdate)

    def generateAccrualSchedule(self):
        
        for dt in self.pmnt_dates:
            x=dt-self.one_month
            x=QuantLib.Date(1,x.month(),x.year())
            self.accrual_start_dates.append(x)
            y=QuantLib.Date.endOfMonth(x)
            self.accrual_end_dates.append(y)

    def mprint(self):
        for i in range(0,len(self.sched_interest)):
            print "%s: %s: %s: Pool Int.:%f Sched Prin:%f Prepaid Prncpal:%f Total Prin:%f" %\
                (self.pmnt_dates[i],self.accrual_start_dates[i],self.accrual_end_dates[i],self.pool_interest[i],\
                self.sched_principal[i],self.prepaid_principal[i],self.total_principal[i])


class FixedRateCF(PoolCF):
    def __init__(self):
        PoolCF.__init__(self)

    def generateCF_CPR_CDR(self,pool,settledate,cpr,cdr,severity):
        PoolCF.generateSMM_SMD_Arr(self,pool,settledate,cpr,cdr,severity)

        wam=pool.wam
        monthly_rate=pool.wac/1200.0
        monthly_cpn=pool.cpn/1200.0
        compound=pow(1.0+monthly_rate,wam)
        total_principal=0.0
        principal=pool.cbal
        monthly_lvl_pmnt=((monthly_rate*compound)/(compound-1))*principal
        
        PoolCF.generatePmntSchedule(self,settledate,wam)
        PoolCF.generateAccrualSchedule(self)
        
        for i in xrange(0,wam):
            self.sched_interest.append(principal*monthly_rate)
            self.pool_interest.append(principal*monthly_cpn)
            self.sched_principal.append(monthly_lvl_pmnt - self.sched_interest[i] )
            self.prepaid_principal.append((principal-self.sched_principal[i])*self.smm_arr[i])
            self.defaulted_principal.append(principal*self.smd_arr[i]*self.severity_arr[i])
            self.total_principal.append(self.sched_principal[i]+self.prepaid_principal[i])
            self.total_cf.append(self.total_principal[i]+self.pool_interest[i])
            principal=principal-self.sched_principal[i]-self.prepaid_principal[i]-self.defaulted_principal[i]
            
            if(i==(wam-1)):
                break

            compound=pow(1.0+monthly_rate,wam-i-1)
            monthly_lvl_pmnt=((monthly_rate*compound)/(compound-1.0))*principal

           

class ArmRateCF(PoolCF):
    def __init__(self):
        PoolCF.__init__(self)
        self.rate_lookback_dates = []

    def generateCF_CPR_CDR(self,pool,settledate,cpr,cdr,severity):
        PoolCF.generateSMM_SMD_Arr(self,pool,settledate,cpr,cdr,severity)
        wam=pool.wam
        lookback=pool.lookback
        PoolCF.generatePmntSchedule(self,settledate,wam)
        PoolCF.generateAccrualSchedule(self)
        self.generateLookBackSchedule(lookback)
            
        monthly_rate=pool.wac/1200.0
        monthly_cpn=pool.cpn/1200.0
        compound=pow(1.0+monthly_rate,wam)
        total_principal=0.0
        principal=pool.cbal
        monthly_lvl_pmnt=((monthly_rate*compound)/(compound-1))*principal
        

        for i in xrange(0,wam):
            self.sched_interest.append(principal*monthly_rate)
            self.pool_interest.append(principal*monthly_cpn)
            self.sched_principal.append(monthly_lvl_pmnt - self.sched_interest[i] )
            self.prepaid_principal.append((principal-self.sched_principal[i])*self.smm_arr[i])
            self.defaulted_principal.append(principal*self.smd_arr[i]*self.severity_arr[i])
            self.total_principal.append(self.sched_principal[i]+self.prepaid_principal[i])
            self.total_cf.append(self.total_principal[i]+self.pool_interest[i])
            principal=principal-self.sched_principal[i]-self.prepaid_principal[i]-self.defaulted_principal[i]
            
            if(i==(wam-1)):
                break

            compound=pow(1.0+monthly_rate,wam-i-1)
            monthly_lvl_pmnt=((monthly_rate*compound)/(compound-1.0))*principal

        
# when generating look back , not only one has to go back 45 days( e.g.)but may also need to go back to monday of that week

    def generateLookBackSchedule(self,lookback):
        del self.rate_lookback_dates[:]
        for dt in self.accrual_start_dates:
            self.rate_lookback_dates.append(dt-lookback*self.one_day)

    def mprint(self):
        for i in range(0,len(self.sched_interest)):
            print "%s: %s: %s: %s Pool Int.:%f Sched Prin:%f Prepaid Prncpal:%f Total Prin:%f" %\
                (self.pmnt_dates[i],self.accrual_start_dates[i],self.accrual_end_dates[i],self.rate_lookback_dates[i],\
                 self.pool_interest[i],\
                 self.sched_principal[i],self.prepaid_principal[i],self.total_principal[i])
                        


def makePoolCF(pool):
    if(pool.type=='ARM'):
        return ArmRateCF()
    else:
        return FixedRateCF()

