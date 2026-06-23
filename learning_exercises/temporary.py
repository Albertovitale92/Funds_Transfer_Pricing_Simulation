import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

FV = 100
T = 10
yields = np.linspace(0.0001, 0.12, 200)

def bond_price(coupon_rate, y):
    C = FV * coupon_rate
    price = sum(C / (1 + y)**t for t in range(1, T+1)) + FV / (1 + y)**T
    return price

def macaulay_duration(coupon_rate, y):
    C = FV * coupon_rate
    CFs = [C for _ in range(T-1)] + [C + FV]
    PVs = [cf / (1 + y)**(t+1) for t, cf in enumerate(CFs)]
    price = sum(PVs)
    weights = [pv / price for pv in PVs]
    D_mac = sum(w * (t+1) for t, w in enumerate(weights))
    return D_mac / (1 + y)

def duration_derivative(coupon_rate, y, h=1e-4):
    # derivata numerica: dD/dy
    return (macaulay_duration(coupon_rate, y + h) - macaulay_duration(coupon_rate, y - h)) / (2*h)

coupon_rates = [0.00, 0.02, 0.05, 0.10]
labels = ["Zero Coupon (0%)", "Low Coupon (2%)", "Medium Coupon (5%)", "High Coupon (10%)"]
colors = ["blue", "orange", "green", "red"]

# --- FIGURE ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10,14))
plt.subplots_adjust(left=0.1, bottom=0.15)

# Linee per i tre grafici
lines_price = [ax1.plot([], [], color=c, label=l, linewidth=2)[0] for c, l in zip(colors, labels)]
lines_dur   = [ax2.plot([], [], color=c, label=l, linewidth=2)[0] for c, l in zip(colors, labels)]
lines_ddur  = [ax3.plot([], [], color=c, label=l, linewidth=2)[0] for c, l in zip(colors, labels)]

# Setup assi
ax1.set_xlim(0, 12)
ax1.set_ylim(20, 200)
ax1.set_title("Curva Prezzo–Yield")
ax1.set_xlabel("Yield (%)")
ax1.set_ylabel("Prezzo")
ax1.grid(True)
ax1.legend()

ax2.set_xlim(0, 12)
ax2.set_ylim(0, 12)
ax2.set_title("Duration vs Yield")
ax2.set_xlabel("Yield (%)")
ax2.set_ylabel("Duration (anni)")
ax2.grid(True)
ax2.legend()

ax3.set_xlim(0, 12)
ax3.set_ylim(-50, 0)
ax3.set_title("Derivata della Duration rispetto al YTM")
ax3.set_xlabel("Yield (%)")
ax3.set_ylabel("dD/dy")
ax3.grid(True)
ax3.legend()

# Slider
ax_slider = plt.axes([0.1, 0.05, 0.8, 0.04])
slider = Slider(ax_slider, "YTM shift (%)", 0, 5, valinit=0)

def update(val):
    shift = slider.val / 100

    for line, c in zip(lines_price, coupon_rates):
        prices = [bond_price(c, y + shift) for y in yields]
        line.set_data(yields*100, prices)

    for line, c in zip(lines_dur, coupon_rates):
        durs = [macaulay_duration(c, y + shift) for y in yields]
        line.set_data(yields*100, durs)

    for line, c in zip(lines_ddur, coupon_rates):
        ddurs = [duration_derivative(c, y + shift) for y in yields]
        line.set_data(yields*100, ddurs)

    fig.canvas.draw_idle()

update(0)
slider.on_changed(update)

plt.show()
