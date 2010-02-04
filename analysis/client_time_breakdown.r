# ============================================================================
# PLOT 1
# Create a stacked bar of the time spent
# ----------------------------------------------------------------------------
# Parameters
#
dataFile <- "monday_night.csv"
test <- "Feb 2"
page <- "Blog"
# ============================================================================
#
# The file looks like this
#
#  test,page,strategy,visitnumber,ttr,datafetch,databulkload,templateparse,latency,bandwidth,date
#  Feb 2,Blog,Sync Kit,1,377,232,16,15,1,1,2010-02-01 21:03:34.337516-05
#
#

data <- read.csv(dataFile,
                header=T,
                dec='.',
                na.strings=c('XXXXXXX')
)

pdf(file="client_time_breakdown.pdf", height=3.5, width=5)

# Filter the table for only rows where the frequency count was 1
# NOTE: In real data set, should also filter for other things, like 
# test and page
filtered <- data[data$test == test,]      
filtered <- data[data$page == page,]      

# Add new column equal to everything left over from TTR
filtered["wire"] = filtered$ttr - filtered$datafetch - filtered$databulkload - filtered$templateparse

# Average the data across each strategy
filteredAgg <- aggregate(filtered, 
                        by=list(filtered$strategy), 
                        FUN=mean, 
                        na.rm=TRUE)

# Note: Group.1 is the name of the aggregation bucket. 
# It would be nice if we could rename this in the 
# aggregate params back to "strategy"
toGraph <- filteredAgg[c("Group.1", "wire", "datafetch", "databulkload", "templateparse")]
print(toGraph)

# Plot them in a stacked bar
# data.matrix converts the data frame into a matrix
# We only extract colums 2-4 because col1 is the strategy name
# We use the transposed column 1 for the names in the argument below
barplot(data.matrix(toGraph[2:5]), 
        main="Client-side Time", 
        ylab="Total Time (ms)", 
        col=heat.colors(4),
        space=0.1, 
        cex.axis=0.8, 
        las=1,
        names.arg=t(toGraph[2:5]), cex=0.8)

