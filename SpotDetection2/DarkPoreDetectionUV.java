import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;

public class My_Plugin implements PlugIn {

	public void run(String arg) {
		ImagePlus imp = IJ.getImage();
		IJ.run(imp, "Color Transformer", "colour=Lab");
		IJ.run("Stack to Images", "");
		imp.close();
		imp.close();
		IJ.run(imp, "8-bit", "");
		IJ.run(imp, "Auto Local Threshold", "method=Niblack radius=15 parameter_1=0 parameter_2=0");
		Prefs.blackBackground = true;
		IJ.run(imp, "Erode", "");
		IJ.run(imp, "Fill Holes", "");
		IJ.run(imp, "Open", "");
		IJ.run(imp, "Close-", "");
		imp.updateAndDraw();

		return imp
	
	}

}
