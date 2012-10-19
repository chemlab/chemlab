def euler(r0, v0, a0, dt):
    dv = a0*dt
    v_n = v0 + dv
    dr = dt*v_n
    r_n = r0 + dr
    return r_n, v_n

