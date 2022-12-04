import subprocess
import pandas as pd
import matplotlib.pyplot as plt

subprocess.call(["./parse_perf_result.sh"])


def get_means():
    receiver = []
    sender = []

    with open("mean.txt", "r") as f:
        for line in f.readlines():
            d = line.strip().split(" ")
            if d[0] == "sender":
                sender.append(float(d[1]))
            elif d[0] == "receiver":
                receiver.append(float(d[1]))
            else:
                print(line, ": Invalid Format")


    data = pd.DataFrame({"sender":sender, "receiver": receiver})
    return data

def get_all():
    data = pd.read_csv("parsed.txt")
    return data

means = get_means().mean()
data = get_all().groupby('interval').mean()
data = data.drop(["0.00-10.00"])
data.plot.bar(rot=30)
plt.plot(data.index,  [means["sender"]]*len(data.index), label="sender mean", color="r")
plt.plot(data.index, [means["receiver"]]*len(data.index), label="receiver mean", color="orange")
plt.legend()
plt.title("Bitrate Complex Network")
plt.xlabel("intervals [sec]")
plt.ylabel("bitrate [Gbits/sec]")
plt.tight_layout()
plt.savefig('fulltopo_clean_bitrate.pdf')
# plt.show()