-- a set of simple (and unlargely untested) scripts for retrieving info from the generators at http://www.seventhsanctum.com/
-- the webclient requires the Beautiful Soup library (http://www.crummy.com/software/BeautifulSoup/)
-- uses python 2.7

example: Ships and Captains
-- generate pirate ship names
> python randominator-webclient.py -g pirateshipnamer -n 10 > ships.csv

-- generate evil names for the captains
> python randominator-webclient.py -g evilnamer -n 10 -c selCategory1:anger selCategory2:ghost selCatergory3:greed > captains.csv

-- merge the docs
> python randominator-merge-tool.py -f ships.csv captains.csv > captains-of-ships.csv

example: Anime style mecha pilots
-- generate names
> python randominator-webclient.py -g quickname -n 5 > mecha-pilots.csv

-- generate character descriptions
> python randominator-webclient.py -g generalperson -n 5 -c selGenType:SEEDANIMEFEMALE> mecha-pilots-desc.csv

-- generate mecha names
> python randominator-webclient.py -g mechaname -n 5 > mecha-models.csv

-- generate humorous powers
> python randominator-webclient.py -g animepowerjoke -n 5 > mecha-powers.csv

-- merge the results
> python randominator-merge-tool.py -f mecha-pilots.csv mecha-pilots.csv mecha-models.csv mecha-powers.csv > mecha-series.csv