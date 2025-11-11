package mysim;

public class MonitorTool {
    private final SimScanner scanner;
    private final SimConnection conn;
    private final Reconnect backoff;
    private final EventHistory history;

    public MonitorTool(EventHistory history) {
        this.scanner = new SimScanner();
        this.conn = new SimConnection();
        this.backoff = new Reconnect();
        this.history = history;
    }

    public Device scanOnce(String name, String addr, int ms) throws InterruptedException {
        return scanner.find(name, addr, ms);
    }

    public boolean connect(Device d) {
        boolean ok = conn.connect(d);
        if (ok) history.record(d, "Connected");
        else history.record(d, "ConnectFailed");
        return ok;
    }

    public void monitor(Device d, long duration) throws InterruptedException {
        long stop = System.currentTimeMillis() + duration;
        while (System.currentTimeMillis() < stop) {
            Thread.sleep(500);
            if (conn.isDisconnected()) {
                history.record(d, "Disconnected");
                backoff.onFailure();
                long wait = backoff.nextDelayMs();
                System.out.println("[Monitor] Retry in " + wait + " ms...");
                Thread.sleep(wait);
                if (conn.connect(d)) {
                    backoff.onSuccess();
                    history.record(d, "Reconnected");
                } else {
                    System.out.println("[Monitor] Reconnect failed");
                }
            }
        }
    }
}
