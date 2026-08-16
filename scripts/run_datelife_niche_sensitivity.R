#!/usr/bin/env Rscript
# Secondary/sensitivity niche-evolution analysis using a DateLife chronogram.
# This is NOT a substitute for the public 405-gene Camellia nuclear backbone.

suppressPackageStartupMessages({
  library(ape)
  library(datelife)
  library(geiger)
  library(nlme)
})

args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 2) stop('usage: run_datelife_niche_sensitivity.R <species_csv> <out_dir>')
infile <- args[[1]]; outdir <- args[[2]]; dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

d <- read.csv(infile, stringsAsFactors=FALSE, check.names=FALSE)
# Exact-taxonomy audit identified Camellia kissi as a fuzzy duplicate of C. kissii.
d <- subset(d, taxon != 'Camellia kissi')
# Main A/W sensitivity only; Y has only two admitted species.
daw <- subset(d, colour_state %in% c('A','W'))
taxa <- unique(daw$taxon)
cat('datelife package version:', as.character(packageVersion('datelife')), '\n')
cat('datelife_use formals:\n')
print(formals(datelife::datelife_use))
cat('Requesting DateLife chronogram for', length(taxa), 'A/W taxa\n')

# Do not force a dating_method at the generic call. CRAN documentation exposes
# dating_method on recent versions, but the installed dispatch observed in CI did
# not accept it. The returned object records whichever method the installed
# package actually used; this analysis is sensitivity-only regardless.
chron <- tryCatch(
  datelife::datelife_use(input=taxa, use_tnrs=TRUE),
  error=function(e) {cat('DATELIFE_ERROR:', conditionMessage(e), '\n'); NULL}
)
if (is.null(chron)) stop('DateLife returned NULL; synthetic chronogram sensitivity unavailable')
if (inherits(chron,'multiPhylo')) {
  cat('DateLife returned', length(chron), 'chronograms; using the first for this declared sensitivity.\n')
  chron <- chron[[1]]
}
if (!inherits(chron,'phylo')) stop('DateLife did not return a phylo object')
chron$tip.label <- gsub('_',' ',chron$tip.label, fixed=TRUE)
write.tree(chron, file=file.path(outdir,'datelife_chronogram.nwk'))

common <- intersect(chron$tip.label, daw$taxon)
cat('Tree tips:', Ntip(chron), '; exact data overlap:', length(common), '\n')
if (length(common) < 20) stop('fewer than 20 exact A/W taxa overlap DateLife tree; sensitivity not admissible')
tr <- drop.tip(chron, setdiff(chron$tip.label, common))
# collapse zero/negative edge issues conservatively
positive_edges <- tr$edge.length[is.finite(tr$edge.length) & tr$edge.length > 0]
if (!length(positive_edges)) stop('DateLife chronogram has no positive branch lengths')
tr$edge.length[tr$edge.length <= 0 | is.na(tr$edge.length)] <- min(positive_edges) * 1e-6

dat <- daw[match(tr$tip.label, daw$taxon),,drop=FALSE]
stopifnot(all(dat$taxon == tr$tip.label))
write.csv(dat, file.path(outdir,'matched_data.csv'), row.names=FALSE)

fit_rows <- list(); gls_rows <- list()
for (metric in c('bio1_median','bio6_median','bio6_q05','bio1_iqr')) {
  y <- setNames(as.numeric(dat[[metric]]), dat$taxon)
  for (model in c('BM','OU','EB')) {
    fit <- tryCatch(geiger::fitContinuous(tr, y, model=model, control=list(niter=100)), error=function(e) {cat('FIT_ERROR',metric,model,conditionMessage(e),'\n'); NULL})
    if (!is.null(fit)) {
      fit_rows[[length(fit_rows)+1]] <- data.frame(
        metric=metric, model=model, lnL=fit$opt$lnL, AICc=fit$opt$aicc,
        sigma2=ifelse(is.null(fit$opt$sigsq),NA,fit$opt$sigsq),
        alpha=ifelse(is.null(fit$opt$alpha),NA,fit$opt$alpha),
        beta=ifelse(is.null(fit$opt$beta),NA,fit$opt$beta), stringsAsFactors=FALSE)
    }
  }
  # Brownian PGLS: thermal metric ~ A versus W state. Data rows are already in
  # exact tree-tip order, so form=~1 avoids fragile row-name evaluation.
  dd <- data.frame(value=as.numeric(dat[[metric]]), state=factor(dat$colour_state, levels=c('W','A')))
  g <- tryCatch(nlme::gls(value ~ state, data=dd,
                          correlation=ape::corBrownian(1, phy=tr, form=~1),
                          method='ML'), error=function(e) {cat('GLS_ERROR',metric,conditionMessage(e),'\n'); NULL})
  if (!is.null(g)) {
    sm <- summary(g)$tTable
    rn <- grep('stateA', rownames(sm), value=TRUE)
    if (length(rn)==1) gls_rows[[length(gls_rows)+1]] <- data.frame(
      metric=metric, model='PGLS_Brownian', n=nrow(dd), estimate_A_minus_W=sm[rn,'Value'],
      SE=sm[rn,'Std.Error'], t=sm[rn,'t-value'], p=sm[rn,'p-value'], stringsAsFactors=FALSE)
  }
}

fits <- if(length(fit_rows)) do.call(rbind,fit_rows) else data.frame()
if(nrow(fits)) {
  fits <- do.call(rbind, lapply(split(fits,fits$metric), function(x){x$deltaAICc <- x$AICc-min(x$AICc,na.rm=TRUE); x[order(x$AICc),]}))
  rownames(fits)<-NULL
}
gls <- if(length(gls_rows)) do.call(rbind,gls_rows) else data.frame()
write.csv(fits,file.path(outdir,'bm_ou_eb_model_fits.csv'),row.names=FALSE)
write.csv(gls,file.path(outdir,'aw_brownian_pgls.csv'),row.names=FALSE)

summary_obj <- list(
  scope='secondary DateLife synthetic-chronogram sensitivity; not the primary Camellia nuclear-phylogeny result',
  datelife_version=as.character(packageVersion('datelife')),
  dating_method=attr(chron,'dating_method'),
  n_requested=length(taxa), n_tree_tips=Ntip(chron), n_exact_overlap=length(common),
  states=as.list(table(dat$colour_state)), ultrametric=is.ultrametric(tr),
  tree_height=max(node.depth.edgelength(tr)),
  best_models=if(nrow(fits)) split(fits[,c('model','AICc','deltaAICc')],fits$metric) else list(),
  pgls=if(nrow(gls)) split(gls,gls$metric) else list()
)
dput(summary_obj, file=file.path(outdir,'summary.dput'))
cat(capture.output(str(summary_obj)), sep='\n')
