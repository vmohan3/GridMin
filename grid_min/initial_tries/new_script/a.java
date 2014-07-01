import java.io.*;
import java.lang.Runtime;
import java.util.ArrayList;
import java.util.Scanner;
class a implements Runnable
{
	static int increment=10;
	static final int M_PI=180;
	static int threadsize;
	static int tasksize;
	static int taskperthread;
	int thread_id;
	public a(int thread_id)
	{
		this.thread_id=thread_id;
	}
	public void run()
	{
		for(long i=0;i<taskperthread;i++)
		{
			
		}
	}
	public static void main(String args[])throws IOException
	{
		if(args.length<1||args.length>2)
		{
			System.out.println("Usage : a #threads [#delta]");
			return;
		}
		if(args.length==2)
		{
			increment=Integer.parseInt(args[1]);
		}
		threadsize = Integer.parseInt(args[0]);
		tasksize=360/increment;
		tasksize=tasksize*tasksize*tasksize*tasksize;	
		taskperthread=tasksize/threadsize;
		System.out.println("Task size : "+tasksize);
		System.out.println("Task per thread : "+taskperthread);
		Runtime r = Runtime.getRuntime();
		ArrayList<String> fl = new ArrayList<String>();
		PrintWriter global=new PrintWriter(new BufferedWriter(new FileWriter("energies.txt")));
		double pp,qq,rr,ss;
		pp=qq=rr=ss=-M_PI;
		for(pp=-M_PI;pp<=M_PI;pp+=increment)
		{
			for(qq=-M_PI;qq<=M_PI;qq+=increment)
			{
				for(rr=-M_PI;rr<=M_PI;rr+=increment)
				{
					for(ss=-M_PI;ss<=M_PI;ss+=increment)
					{
						System.out.println("pp = "+pp+", qq = "+qq+", rr = "+rr+", ss = "+ss);		
						BufferedWriter x=new BufferedWriter(new FileWriter("scripter"));
						PrintWriter p=new PrintWriter(x);
						p.println("sed \'s/__angle1__/"+pp+"/\' <temp >>temp1");
						p.println("rm temp");
						p.println("sed \'s/__angle2__/"+qq+"/\' <temp1 >>temp");	
						p.println("rm temp1");
						p.println("sed \'s/__angle3__/"+rr+"/\' <temp >>temp1");	
						p.println("rm temp");
						p.println("sed \'s/__angle4__/"+ss+"/\' <temp1 >>temp");
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
								synchronized(a.class)
								{
									global.println(split_line[2]);
									break;
								}
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
			}
		}
		global.close();
	}
}
