"""Render three peak RSS report figures from recorded statistics, without benchmarks."""
import argparse
import json
import math
from pathlib import Path
import sys
from plot_clt_report import BASE, EXPERIMENTS, sha, plt, matplotlib

DESIGNS = [
    ('original-file-count', EXPERIMENTS[0][1], ['count-1','count-4','count-16','count-32'],
     [1,4,16,32], ['1','4','16','32'], 'Number of Files', 'Number of Context Files',
     [352.422,352.078,351.852,352.539], (340,365)),
    ('original-input-size', EXPERIMENTS[0][1], EXPERIMENTS[0][2], EXPERIMENTS[0][3],
     EXPERIMENTS[0][4], 'Input Size', 'Total Context Input Size (log scale)',
     [351.695,352.086,352.266,352.703], (340,365)),
    ('extension-input-size', EXPERIMENTS[1][1], EXPERIMENTS[1][2], EXPERIMENTS[1][3],
     EXPERIMENTS[1][4], 'Input Size', 'Total Context Input Size (log scale)',
     [351.914,353.039,357.234,384.750,474.445], (330,520)),
]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=BASE/'analysis/report-figures')
    args=parser.parse_args()
    targets=[args.output/f'peak-rss-{d[0]}.{ext}' for d in DESIGNS for ext in ['png','pdf','svg']]
    manifest_path=args.output/'peak-rss-manifest.json'
    checksum_path=args.output/'peak-rss-sha256.json'
    if any(p.exists() for p in [*targets,manifest_path,checksum_path]):
        parser.error('Choose a new output directory; existing artifacts are preserved.')
    sources={str(d[1].relative_to(BASE)):sha(d[1]) for d in DESIGNS}
    selected={}
    for key,source,ids,x,labels,dimension,xlabel,reference,limits in DESIGNS:
        summary=json.loads(source.read_text())
        index={r['scenario']:r for r in summary};assert len(index)==len(summary)
        rows=[index[i] for i in ids]
        for row,xx,expected in zip(rows,x,reference):
            count_design=dimension=='Number of Files'
            assert row['count']==(xx if count_design else 4)
            assert row['bytes']==(65536 if count_design else xx)
            values=row['peakRSSMiB']
            assert row['failures']==0 and values['n']==30
            assert round(values['median'],3)==expected
            assert all(math.isfinite(v) for v in [values['median'],values['p90'],*values['medianCI95']])
            assert values['medianCI95'][0]<=values['median']<=values['medianCI95'][1]
        selected[key]=rows
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
        'axes.labelsize':11.5,'xtick.labelsize':11,'ytick.labelsize':11,
        'legend.fontsize':10,'figure.facecolor':'white','axes.facecolor':'white',
        'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})
    args.output.mkdir(parents=True,exist_ok=True)
    verified={}
    for key,source,ids,x,labels,dimension,xlabel,reference,limits in DESIGNS:
        rows=selected[key];median=[r['peakRSSMiB']['median'] for r in rows]
        p90=[r['peakRSSMiB']['p90'] for r in rows]
        low=[r['peakRSSMiB']['medianCI95'][0] for r in rows]
        high=[r['peakRSSMiB']['medianCI95'][1] for r in rows]
        fig,ax=plt.subplots(figsize=(9,5.5),layout='constrained')
        med=ax.errorbar(x,median,yerr=[[m-l for m,l in zip(median,low)],
            [h-m for m,h in zip(median,high)]],fmt='o-',color='#1764ab',linewidth=1.8,
            markersize=6,capsize=4,elinewidth=1.5,zorder=3)
        tail,=ax.plot(x,p90,'s--',color='#d06a00',linewidth=1.8,markersize=6,zorder=2)
        experiment='Extension' if key.startswith('extension') else 'Original'
        ax.set_title(f'Peak Memory Usage (RSS) vs. {dimension} — {experiment} Experiment',pad=14)
        ax.set_xlabel(xlabel,labelpad=9);ax.set_ylabel('Peak Memory Usage (RSS, MiB)',labelpad=9)
        if dimension=='Input Size':ax.set_xscale('log',base=2)
        ax.set_xticks(x,labels);ax.minorticks_off();ax.set_ylim(*limits)
        ax.set_yticks([340,345,350,355,360,365] if experiment=='Original' else [350,375,400,425,450,475,500])
        ax.grid(True,color='#b8c0c8',alpha=.28,linewidth=.7)
        ax.spines[['top','right']].set_visible(False)
        legend=ax.legend([med,tail],['Median (95% Bootstrap CI)','90th Percentile (P90)'],
            loc='upper left',frameon=True,framealpha=1,facecolor='white',edgecolor='#cccccc')
        assert list(med.lines[0].get_ydata())==median and list(tail.get_ydata())==p90
        for i,segment in enumerate(med.lines[2][0].get_segments()):
            assert all(math.isclose(v,w,rel_tol=0,abs_tol=1e-10) for v,w in zip(segment[:,1],[low[i],high[i]]))
        assert not ax.texts and not fig.texts
        assert [t.get_text() for t in legend.get_texts()]==['Median (95% Bootstrap CI)','90th Percentile (P90)']
        fig.canvas.draw()
        for text in [ax.title,ax.xaxis.label,ax.yaxis.label,*ax.get_xticklabels(),*ax.get_yticklabels()]:
            box=text.get_window_extent();bounds=fig.bbox
            assert box.x0>=bounds.x0-1 and box.y0>=bounds.y0-1 and box.x1<=bounds.x1+1 and box.y1<=bounds.y1+1, 'Clipped label'
        for ext in ['png','pdf','svg']:fig.savefig(args.output/f'peak-rss-{key}.{ext}',dpi=300)
        plt.close(fig)
        verified[key]=[{'scenario':r['scenario'],'files':r['count'],'bytes':r['bytes'],
            'median':m,'p90':p,'medianCI95':[l,h]} for r,m,p,l,h in zip(rows,median,p90,low,high)]
    assert sources=={str(d[1].relative_to(BASE)):sha(d[1]) for d in DESIGNS}
    manifest={'source_sha256':sources,'script_sha256':sha(Path(__file__)),
        'style_reference_sha256':sha(Path(__file__).with_name('plot_clt_report.py')),
        'python':sys.version,'matplotlib':matplotlib.__version__,'invocation':sys.argv,
        'png_dpi':300,'size_inches':[9,5.5],
        'boundary':'Actual CLI PID lifetime high-water RSS through local Config/chat-initialized readiness, before fixture validation/inference. Excludes parent/helper RSS and is not refresh-exclusive memory or V8 heap usage.',
        'statistics':'Existing peakRSSMiB median, P90 and bootstrap median CIs reused without recalculation. Original and extension sessions kept separate.',
        'validation':'Recorded values, actual plot artists and CI endpoints checked; exact legend; no annotations/footers or clipped labels.',
        'plotted_values':verified}
    manifest_path.write_text(json.dumps(manifest,indent=2))
    checksum_path.write_text(json.dumps({p.name:sha(p) for p in [*targets,manifest_path]},indent=2))
    print('Generated and validated three figures in PNG/PDF/SVG:',args.output)

if __name__=='__main__':main()
