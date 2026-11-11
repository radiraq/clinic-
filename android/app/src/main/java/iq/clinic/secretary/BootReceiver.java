package iq.clinic.secretary;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** After a restart, reopen the app so alerts keep arriving. */
public class BootReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context c, Intent i) {
        if (!Intent.ACTION_BOOT_COMPLETED.equals(i.getAction())) return;
        if (c.getSharedPreferences("app", Context.MODE_PRIVATE).getString("clinic", null) == null) return;
        BellService.start(c);
    }
}
