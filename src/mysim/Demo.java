package mysim;

public class Demo {
    public static void main(String[] args) throws Exception {
        System.out.println("=== TruTooth Bluetooth Reconnect Simulation ===");
        EventHistory history = new EventHistory();
        MonitorTool monitor = new MonitorTool(history);

        String targetName = "MySpeaker";
        String targetAddr = null;

        Device dev = null;
        while (dev == null) {
            System.out.println("[Demo] Scanning...");
            dev = monitor.scanOnce(targetName, targetAddr, 3000);
            if (dev == null) {
                System.out.println("[Demo] Not found, retry in 3s...");
                Thread.sleep(3000);
            }
        }

        System.out.println("[Demo] Found: " + dev.shortStr());
        if (!monitor.connect(dev)) {
            System.out.println("[Demo] Initial connection failed.");
            return;
        }

        System.out.println("[Demo] Monitoring connection for 45 seconds...");
        monitor.monitor(dev, 45000L);
        history.printAll();
        System.out.println("=== End Simulation ===");
    }
}
