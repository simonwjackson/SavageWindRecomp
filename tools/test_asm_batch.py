"""emit_asm_batch: the register a batch carries NZCV in never also holds a guest register or a constant.

Usage: test_asm_batch.py (no game files needed)
"""
import re

from lifter import AsmInsn, emit_asm_batch


def ldr_s(rt, rn):  # ldr s<rt>, [x<rn>, #0xa8]
    return 0xbd400000 | ((0xa8 // 4) << 10) | (rn << 5) | rt


def mapped(asm):
    # guest register -> host scratch, from the batch's loads ldr x<s>, [%0, #<8 * g>]
    return {int(off) // 8: int(s) for s, off in re.findall(r'ldr x(\d+), \[%0, #(\d+)\]', asm) if int(off) < 256}


def check(n, flags):
    batch = [AsmInsn(ldr_s(0, 0), {0}, [(5, g)]) for g in range(n)]
    batch[-1].flags = flags
    asm = emit_asm_batch(batch)
    regs = mapped(asm)
    assert len(regs) == n, (n, flags, regs)
    if flags:
        assert 16 not in regs.values(), f'{n} guest registers with flags: x16 holds one and NZCV ({regs})'
        assert asm.count('ldr x16, [%0, #272]') == 1
    return regs


def main():
    for n in range(1, 9):
        check(n, False)
        check(n, True)
    # without flags all nine scratch registers stay available, as before
    assert 16 in check(9, False).values()
    print('ok: asm batch scratch registers')


if __name__ == '__main__':
    main()
