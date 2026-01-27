import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { Cpu, HardDrive, MemoryStick } from "lucide-react";

export default function SystemResources({ resources }) {
  const cpuData = [
    { name: "Used", value: resources.cpu_percent },
    { name: "Free", value: 100 - resources.cpu_percent },
  ];

  const memoryData = [
    { name: "Used", value: resources.memory_used_gb },
    { name: "Free", value: resources.memory_total_gb - resources.memory_used_gb },
  ];

  const diskData = [
    { name: "Used", value: resources.disk_used_gb },
    { name: "Free", value: resources.disk_total_gb - resources.disk_used_gb },
  ];

  const COLORS = {
    cpu: ["#10b981", "#27272a"],
    memory: ["#3b82f6", "#27272a"],
    disk: ["#f59e0b", "#27272a"],
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border/50 rounded-sm p-2 shadow-lg">
          <p className="font-mono text-xs text-foreground">
            {payload[0].name}: {payload[0].value.toFixed(2)}
            {payload[0].name.includes("GB") ? "GB" : "%"}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-sm p-6 tactical-corner mb-8" data-testid="system-resources-panel">
      <h2 className="font-secondary font-bold text-2xl tracking-tight uppercase text-foreground mb-6">
        System Resources
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* CPU */}
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4">
          <div className="flex items-center gap-2 mb-4">
            <Cpu className="text-primary" size={20} />
            <h3 className="font-secondary font-semibold text-lg uppercase tracking-wider text-foreground">
              CPU
            </h3>
          </div>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height={192}>
              <PieChart>
                <Pie
                  data={cpuData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {cpuData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS.cpu[index]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-center mt-2">
            <div className="font-mono text-2xl font-bold text-primary" data-testid="cpu-usage">
              {resources.cpu_percent.toFixed(1)}%
            </div>
            <div className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
              CPU Usage
            </div>
          </div>
        </div>

        {/* Memory */}
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4">
          <div className="flex items-center gap-2 mb-4">
            <MemoryStick className="text-[#3b82f6]" size={20} />
            <h3 className="font-secondary font-semibold text-lg uppercase tracking-wider text-foreground">
              Memory
            </h3>
          </div>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height={192}>
              <PieChart>
                <Pie
                  data={memoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {memoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS.memory[index]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-center mt-2">
            <div className="font-mono text-2xl font-bold text-[#3b82f6]" data-testid="memory-usage">
              {resources.memory_percent.toFixed(1)}%
            </div>
            <div className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
              {resources.memory_used_gb.toFixed(1)}GB / {resources.memory_total_gb.toFixed(1)}GB
            </div>
          </div>
        </div>

        {/* Disk */}
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4">
          <div className="flex items-center gap-2 mb-4">
            <HardDrive className="text-accent" size={20} />
            <h3 className="font-secondary font-semibold text-lg uppercase tracking-wider text-foreground">
              Disk
            </h3>
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={diskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {diskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS.disk[index]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-center mt-2">
            <div className="font-mono text-2xl font-bold text-accent" data-testid="disk-usage">
              {resources.disk_percent.toFixed(1)}%
            </div>
            <div className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
              {resources.disk_used_gb.toFixed(1)}GB / {resources.disk_total_gb.toFixed(1)}GB
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}