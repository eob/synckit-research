
# ============================================================================
# Read in the sample data set
# ============================================================================

data <- read.csv("sample.csv",
    header=T,
    dec='.',
    na.strings=c('XXXXXXX')
)

# ============================================================================
# PLOT 1
# Create a stacked bar of the time spent when the frequency was 1
# ============================================================================

# Filter the table for only rows where the frequency count was 1
# NOTE: In real data set, should also filter for other things, like test and page
freqOne <- data[data$freq == 1,]      

# Add new column equal to everything left over from TTR
freqOne["wire"] = freqOne$ttr - freqOne$dom - freqOne$db

# Average the data across each strategy
freqOneAgg <- aggregate(freqOne, by=list(freqOne$strategy), FUN=mean, na.rm=TRUE)

# Add a new column that is eqal to the TTR minus the others
# Note: Group.1 is the name of the aggregation bucket. 
# It would be nice if we could rename this in the aggregate params back to "strategy"
freqOneFiltered <- freqOneAgg[c("Group.1", "wire", "dom", "db")]

# Plot them in a stacked bar
# data.matrix converts the data frame into a matrix
# We only extract colums 2-4 because col1 is the strategy name
# We use the transposed column 1 for the names in the argument below
barplot(data.matrix(freqOneFiltered[2:4]), 
        main="Client-side Time", 
        ylab="Total Time (ms)", 
        col=heat.colors(4),
        space=0.1, 
        cex.axis=0.8, 
        las=1,
        names.arg=t(freqOneFiltered[1:1]), cex=0.8)
