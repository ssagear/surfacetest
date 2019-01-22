

import matplotlib.pyplot as plt
import numpy as np

#229227260
#213244700
#229227268

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]


deff_1 = .825358
#deff_1 = .90
#deff_2 = 1
#deff_3 = 1
eta = np.arange(0, 1, .001)
t_p = .035
n_stars = 500
impact = .57

p_1 = eta*t_p*impact*deff_1

#p_2 = eta*t_p*deff_2
#print(p_2)

#p_3 = eta*t_p*deff_3

p_null = (1-p_1)**n_stars
#print(p_null)

#####
p=.05
#####

p_close = find_nearest(p_null, p)

p_null_lst = p_null.tolist()

p_ind = p_null_lst.index(p_close)

eta_p = eta[p_ind]


fig, ax = plt.subplots()

ax.plot(eta, p_null)
ax.set_ylim(0, 1)
ax.set_xlabel('$\eta$')
ax.set_ylabel('$\mathregular{P_{null}}$')
ax.set_title('$P_{null}$ vs $\eta$: detection efficiency 82.54%')

ax.scatter(eta_p, p_close)

ax.text(.60, .88, '$\mathregular{P_{null}}$ = ' + str(p) + '\n$\eta$ = ' + str(round(eta_p, 4)))
ax.text(.60, .83, 'Planets from .3 to .35 $R_{p}/R_{s}$')
ax.text(.60, .78, 'and 1 to 1.58 day periods')
plt.show()
