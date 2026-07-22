library(lavaan)
library(semTools)
library(dplyr)
data <- read.csv("data/chapter18_sem_data.csv")
partial_model <- '
 Preparation =~ prep1 + prep2 + prep3
 SelfEfficacy =~ eff1 + eff2 + eff3
 Performance =~ perf1 + perf2 + perf3
 SelfEfficacy ~ a*Preparation
 Performance ~ b*SelfEfficacy + direct*Preparation
 indirect := a*b
 total := direct + indirect
'
full_model <- '
 Preparation =~ prep1 + prep2 + prep3
 SelfEfficacy =~ eff1 + eff2 + eff3
 Performance =~ perf1 + perf2 + perf3
 SelfEfficacy ~ a*Preparation
 Performance ~ b*SelfEfficacy
 indirect := a*b
'
direct_model <- '
 Preparation =~ prep1 + prep2 + prep3
 SelfEfficacy =~ eff1 + eff2 + eff3
 Performance =~ perf1 + perf2 + perf3
 SelfEfficacy ~ a*Preparation
 Performance ~ direct*Preparation
'
fit1 <- sem(partial_model,data=data,estimator="MLR",missing="fiml")
fit2 <- sem(full_model,data=data,estimator="MLR",missing="fiml")
fit3 <- sem(direct_model,data=data,estimator="MLR",missing="fiml")
summary(fit1,fit.measures=TRUE,standardized=TRUE,rsquare=TRUE,ci=TRUE)
lavTestLRT(fit1,fit2,method="satorra.bentler.2001")
lavTestLRT(fit1,fit3,method="satorra.bentler.2001")
standardizedSolution(fit1)
inspect(fit1,"r2")
resid(fit1,type="cor")
modindices(fit1,sort.=TRUE,minimum.value=3.84)
compRelSEM(fit1)
AVE(fit1)
fit_boot <- sem(partial_model,data=data,estimator="ML",missing="fiml",se="bootstrap",bootstrap=5000,fixed.x=FALSE)
parameterEstimates(fit_boot,standardized=TRUE,ci=TRUE,boot.ci.type="bca.simple") |> filter(label %in% c("a","b","direct","indirect","total"))