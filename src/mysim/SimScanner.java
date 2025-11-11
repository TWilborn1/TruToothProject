package mysim;

import java.util.Random;

public class SimScanner {
    private final Random rng = new Random();

    public Device find(String wantedName, String wantedAddr, int scanMs) throws InterruptedException {
        System.out.println("[Scanner] scanning for " + scanMs + " ms...");
        Thread.sleep(Math.min(scanMs, 1000));
        boolean found = rng.nextDouble() < 0.5;
        if (!found) return null;

        String name = wantedName != null ? wantedName : "Speaker-" + hex2();
        String addr = wantedAddr != null ? wantedAddr : randomAddr();
        return new Device(name, addr);
    }

    private String randomAddr() {
        return hex2()+":"+hex2()+":"+hex2()+":"+hex2()+":"+hex2()+":"+hex2();
    }
    private String hex2() { return String.format("%02X", rng.nextInt(256)); }
}
