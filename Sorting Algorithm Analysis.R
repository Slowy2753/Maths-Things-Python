library(tidyverse)

merge_tide <- pivot_longer(mergeSortTimes,
             c(2:100),
             names_to='Run',
             values_to = 'Sort_Time')
merge_tide$sort <- 'merge'

select_tide <- pivot_longer(selectionSortTimes,
                            c(2:100),
                            names_to='Run',
                            values_to = 'Sort_Time')
select_tide$sort<- 'select'

big_boi <- rbind(merge_tide, select_tide)


ggplot(big_boi, aes(x=V1, y=Sort_Time))+
  geom_point(aes(col=sort),size=0.2)+
  geom_smooth(aes(col=sort))+
  ylim(0,2*10^6)+
  xlab("Array Size")
  
ggplot(big_boi, aes(x=V1, y=Sort_Time))+
  geom_smooth(aes(col=sort))+
  ylim(0,2*10^6)+
  xlab("Array Size")

