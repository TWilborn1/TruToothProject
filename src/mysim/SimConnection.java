package mysim;

import java.util.Random;

public class SimConnection {
    private final Random rng = new Random();
    private boolean connected = false;
    private long dropAt = -1L;

    public boolean connect(Device d) {
        try { Thread.sleep(200 + rng.nextInt(300)); } catch (InterruptedException ignore) {}
        boolean ok = rng.nextDouble() < 0.85;
        if (ok) {
            connected = true;
            scheduleDrop();
            System.out.println("[SimConnection] Connected to " + d.shortStr());
        }
        return ok;
    }

    public boolean isDisconnected() {
        if (connected && dropAt > 0 && System.currentTimeMillis() >= dropAt) {
            connected = false;
            dropAt = -1L;
            System.out.println("[SimConnection] Link drop happened.");
            return true;
        }
        return !connected;
    }

    private void scheduleDrop() {
        long now = System.currentTimeMillis();
        long delay = 5000 + rng.nextInt(8000);
        dropAt = now + delay;
    }
}
