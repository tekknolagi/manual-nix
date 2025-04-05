FROM nixos/nix
RUN nix-channel --update
COPY pix.py pix.py
RUN /nix/store/zv1kaq7f1q20x62kbjv6pfjygw5jmwl6-python3-3.12.7/bin/python3 pix.py
CMD cat /nix/store/5bkcqwq3qb6dxshcj44hr1jrf8k7qhxb-simple
