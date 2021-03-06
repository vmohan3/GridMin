import java.io.*;
import java.lang.Runtime;
import java.util.ArrayList;
import java.util.Scanner;
class a
{
	static final double increment=0.104719755;
	static final double M_PI=3.141592654;
	public static void main(String args[])throws IOException
	{
		Runtime r = Runtime.getRuntime();
		ArrayList<String> fl = new ArrayList<String>();
		PrintWriter global=new PrintWriter(new BufferedWriter(new FileWriter("energies.txt")));
		double pp,qq,rr,ss;
		pp=qq=rr=ss=-M_PI;
	
		for(qq=-M_PI;qq<=M_PI;qq+=increment)
		{
		for(rr=-M_PI;rr<=M_PI;rr+=increment)
		{
			System.out.println("qq = "+qq+", rr = "+rr);		
			BufferedWriter x=new BufferedWriter(new FileWriter("scripter"));
			PrintWriter p=new PrintWriter(x);
			p.println("sed \'s/__angle2__/"+qq+"/\' <temp >>temp1");	
			p.println("rm temp");
			p.println("sed \'s/__angle3__/"+rr+"/\' <temp1 >>temp");	
			p.println("rm temp1");
			p.close();
			try
			{
				String cmd = "cp bkp temp";
				ProcessBuilder pb = new ProcessBuilder("bash", "-c", cmd);
				Process shell = pb.start();
				shell.waitFor();
				cmd="chmod 755 scripter";
				pb=new ProcessBuilder("bash", "-c", cmd);
				shell=pb.start();
				shell.waitFor();
				cmd="./scripter";
                                pb=new ProcessBuilder("bash", "-c", cmd);
                                shell=pb.start();
                                shell.waitFor();
				cmd="./run";
                                pb=new ProcessBuilder("bash", "-c", cmd);
                                shell=pb.start();
                                shell.waitFor();
				cmd="rm scripter";
                                pb=new ProcessBuilder("bash", "-c", cmd);
                                shell=pb.start();
                                shell.waitFor();
				cmd="rm temp";
                                pb=new ProcessBuilder("bash", "-c", cmd);
                                shell=pb.start();
                                shell.waitFor();
				cmd="rm toph19_5fs_20k_ui.gromacs.trj0.psf";
                                pb=new ProcessBuilder("bash", "-c", cmd);
                                shell=pb.start();
                                shell.waitFor();
				cmd="rm toph19_5fs_20k_ui.gromacs.trj0.pdb";
                                pb=new ProcessBuilder("bash", "-c", cmd);
                                shell=pb.start();
                                shell.waitFor();
			}
			catch(Exception e)
			{
			}	
			File f=new File("i.txt");
			Scanner _scan = new Scanner(new BufferedInputStream(new FileInputStream(f)));
			while(_scan.hasNextLine())
			{
				String line=_scan.nextLine();
				fl.add(line);
			}
			for(int j=fl.size()-1;j>=0;j--)
			{
				String line=fl.get(j);
				if (line.trim().length() == 0)
				   continue;
				String[] split_line = line.split("\\s+");
				if(split_line[0].equalsIgnoreCase("ABNR>"))
				{
					global.println(qq+"\t"+rr+"\t"+split_line[2]);
					break;
				}
			}
			_scan.close();
			fl.clear();
			try
			{
				String cmd = "rm i.txt";
                                ProcessBuilder pb = new ProcessBuilder("bash", "-c", cmd);
                                Process shell = pb.start();
                                shell.waitFor();
			}
			catch(Exception e)
			{
			}
		}
		}
		global.close();
	}
}
